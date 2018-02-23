import { Component, OnInit, Input } from '@angular/core';

import { LocationService } from '../location.service';
import { MemberService } from '../member.service';

import { Globals } from '../globals';

@Component({
  selector: 'media-search-bar',
  templateUrl: './media-search-bar.component.html',
  styleUrls: ['./media-search.component.css']
})
export class MediaSearchBarComponent implements OnInit {
  items: any[] = []; // items to show in enumerating search results
  cont: number = 0;
  
  msg: string;
  query: any = null; // search query
  
  title: string; // media attributes
  author: string;
  genre: string;
  type_: string;

  _title: string; // 'pseudo'-versions of the above vars for displaying
  _author: string;
  _genre: string;
  _type_: string;
  
  PAGELEN: number = 5; // perhaps subject to change
  
  @Input() heading: string; // message that shows up top
  @Input() default: string = 'blank'; // if 'all', shows all of location's items when query is blank
  @Input('with-delete') forbidDeletion: boolean = true; // opposite trick like in tooltip.component; controls whether the red (delete) link shows
  
  constructor(
    public globals: Globals,
    private locationService: LocationService,
    private memberService: MemberService
  ) {}

  ngOnInit() {
    if (this.default == 'all') {
      this.getAllItems(true);
    }
  }
  
  reset() {
    this.query = this.cont = this.title = this.author = this.genre = this.type_ = null;
    if (this.default == 'all') {
      this.getAllItems(true);
    }
  }
  
  del(mID) {
    this.locationService.deleteItem(mID)
      .subscribe(
        resp => this.msg = 'Deleted successfully.',
        err => this.msg = err.error?err.error:'Error.',
        () => this.search(false)
      );
  }
  
  getAllItems(reset: boolean = false) {
    if (reset) { this.cont = 0; }
    this.locationService.getAllMedia(this.cont)
      .subscribe(resp => this.items = resp.items, err => this.msg = err.error?err.error:'Error.');
  }
  
  checkVisible(): boolean {
    return [this.title, this.author, this.genre, this.type_].some(a => a && a != 'null');
  }
  
  search(reset: boolean = false) {
    if (this.default == 'all' && !this.checkVisible()) {
      this.getAllItems(reset);
      return;
    }
    if (reset) { this.cont = 0; }
    this.locationService.searchMedia(this.cont, this.title, this.author, this.genre, this.type_)
      .subscribe(
        resp => {
          this.query = {
            page: this.cont/this.PAGELEN,
            title: this.title,
            author: this.author,
            genre: this.genre,
            type_: this.type_
          }
          this.items = resp;
          this._title = this.title;
          this._author = this.author;
          this._genre = this.genre;
          this._type_ = this.type_;
        },
        err => {
          this.msg = err.error?err.error:'Error.';
        }
      );
  }
}
