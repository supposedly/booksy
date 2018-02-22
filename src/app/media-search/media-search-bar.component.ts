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
  items: any[] = [];
  cont: number = 0;
  
  msg: string;
  query: any;
  
  title: string;
  author: string;
  genre: string;
  type_: string;

  _title: string;
  _author: string;
  _genre: string;
  _type_: string;
  
  @Input() heading: string;
  @Input('manage') notManaging: true;
  @Input('all-items') showAll: true;
  
  constructor(
    public globals: Globals,
    private locationService: LocationService,
    private memberService: MemberService
  ) {}

  ngOnInit() {
    if (this.showAll) {
      this.getAllItems(true);
    }
  }
  
  reset() {
    this.title = this.author = this.genre = this.type_ = null;
    this.getAllItems();
  }
  
  getAllItems(reset: boolean = false) {
    if (reset) { this.cont = 0; }
    this.locationService.getAllMedia(this.cont)
      .subscribe(resp => this.items = resp.items);
  }
  
  checkVisible(): boolean {
    return [this.title, this.author, this.genre, this.type_].some(a => !!((a != 'null') && a));
  }
  
  search(reset: boolean = false) {
    if (reset) { this.cont = 0; }
    if (![this.title, this.author, this.genre, this.type_].some(a => !!a)) {
      this.getAllItems(true);
      return null;
    }
    this.locationService.searchMedia(this.cont, this.title, this.author, this.genre, this.type_)
      .subscribe(
        resp => {
          this.query = {
            page: this.cont/20,
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
