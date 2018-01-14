import { Component, OnInit, Input } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Location } from '@angular/common';

import { MediaItem } from '../classes';
import { MediaService } from '../media.service';

import { Globals } from '../globals';

@Component({
  selector: 'app-media-info',
  templateUrl: './media-info.component.html',
  styleUrls: ['./media-info.component.css']
})
export class MediaInfoComponent implements OnInit {
  item: MediaItem;
  mID: string;
  msg: string;
  
  constructor(
    public globals: Globals,
    public location: Location,
    private route: ActivatedRoute,
    private mediaService: MediaService
  ) {}
  
  ngOnInit(): void {
    this.mID = this.route.snapshot.paramMap.get('mID');
    this.getItem();
  }
  
  getItem(): void {
    this.mediaService.getInfo(this.mID)
      .subscribe(item => this.item = item.info);
  }
  
  placeOnHold(): void {
    this.mediaService.placeHold(this.mID)
      .subscribe(resp => {}, err => this.msg = err.error?err.error:'Error.');
  }

}
