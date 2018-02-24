import { Component, OnInit, Input } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Location } from '@angular/common';

import { LocationService } from '../location.service';
import { MediaService } from '../media.service';

import { Globals } from '../globals';

@Component({
  selector: 'app-media-edit',
  templateUrl: './media-edit.component.html',
  styleUrls: ['./media-edit.component.css']
})
export class MediaEditComponent implements OnInit {
  item: any;
  mID: string;
  genre_: string = null;
  msg: string;
  
  constructor(
    public globals: Globals,
    public location: Location,
    private route: ActivatedRoute,
    private locationService: LocationService,
    private mediaService: MediaService
  ) {}
  
  ngOnInit(): void {
    this.mID = this.route.snapshot.paramMap.get('mID');
    if (this.mID == 'new') {
      this.makeItem();
    } else {
      this.getItem();
    }
  }
  
  getItem(): void {
    this.mediaService.getInfo(this.mID)
      .subscribe(item => this.item = item.info);
  }
  
  makeItem(): void {
    this.item = {
      mid: null,
      title: 'New item',
      author: null,
      published: null,
      image: null,
      type: null,
      genre: null,
      isbn: null,
      price: null,
      length: null,
      available: null,
    }
  }
  
  checkAllNecessary() {
    // ugly
    let item = this.item;
    return (item.isbn || (item.title && item.author)) && (this.genre_ || item.genre) && item.type && item.price && item.length;
  }
  
  submit(): void {
    if (this.genre_) { // add a new genre
      this.globals.locGenres.push(this.genre_);
      this.item.genre = this.genre_;
    }
    if (this.mID == 'new') {
      this.locationService.addItem(this.item)
        .subscribe(
          resp => {
            this.item.image = resp.image;
            this.mID = resp.mid;
            this.item.mid = resp.mid;
            this.msg = 'Successfully created.'
          },
          err => {
            this.msg = err.error?err.error:'Error.'
          }
        );
    } else {
      this.mediaService.editItem(this.item)
        .subscribe(resp => this.msg = 'Successfully edited.', err => this.msg = err.error?err.error:'Error.')
    }
  }
}
